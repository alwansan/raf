#if UNITY_ANDROID && !UNITY_EDITOR
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using UnityEngine.UI;
using TouchPhase = UnityEngine.InputSystem.TouchPhase;

namespace RaftAndroid.Platform
{
    // Filter outside touches BEFORE InputSystemUIInputModule can see a left
    // touch press. Original interactive UI and authored controller/editor surfaces retain touch events.
    // Physical mouse/keyboard/gamepad events are never intercepted or removed.
    public sealed class AndroidTouchPointer : MonoBehaviour
    {
        private static AndroidTouchPointer instance;
        private Mouse mouse;
        private TouchPointerGesture gesture;
        private TouchPointerButtons buttons;
        private Vector2 position;
        private int pressedFrame = -1, releasedFrame = -1;
        private bool suspended;
        private readonly HashSet<int> uiTouches = new HashSet<int>();
        private readonly List<RaycastResult> hits = new List<RaycastResult>(16);

        private void OnEnable()
        {
            instance = this;
            // Matches original CustomInputConfig, including before its OnEnable.
            Input.simulateMouseWithTouches = false;
            mouse = InputSystem.AddDevice<Mouse>("RaftAndroidTouchLeft");
            buttons = new TouchPointerButtons(SetButton);
            gesture = new TouchPointerGesture(Command);
            InputSystem.onEvent += OnEvent;
            InputSystem.onBeforeUpdate += BeforeInput;
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", "touch_pointer_ready", "holdMs=500; button=left; automaticTouchMouseSimulation=false; actualDeviceExecutionVerified=false");
        }

        private bool OwnedUi(Vector2 point)
        {
            var events = EventSystem.current;
            if (events == null) return false;
            hits.Clear();
            events.RaycastAll(new PointerEventData(events) { position = point }, hits);
            foreach (var hit in hits)
            {
                var target = hit.gameObject;
                if (target == null) continue;
                // Keep authored controller/editor/HUD touches with their UI module.
                if (target.transform.IsChildOf(transform)) return true;
                // Ignore PhysicsRaycaster hits and decorative full-screen HUD
                // graphics: neither should turn gameplay touch into UI.
                if (!(hit.module is GraphicRaycaster)) continue;
                // Original UGUI menus are NOT children of the Android host.
                // Preserve their actual interactive pointer/drag/scroll targets.
                if (ExecuteEvents.GetEventHandler<IPointerClickHandler>(target) != null ||
                    ExecuteEvents.GetEventHandler<IPointerDownHandler>(target) != null ||
                    ExecuteEvents.GetEventHandler<IPointerUpHandler>(target) != null ||
                    ExecuteEvents.GetEventHandler<IBeginDragHandler>(target) != null ||
                    ExecuteEvents.GetEventHandler<IDragHandler>(target) != null ||
                    ExecuteEvents.GetEventHandler<IScrollHandler>(target) != null)
                    return true;
            }
            return false;
        }

        private void OnEvent(InputEventPtr input, InputDevice device)
        {
            var screen = device as Touchscreen;
            if (screen == null || input.handled || !input.IsA<StateEvent>()) return;
            // Touchscreen's 1.7 state callback maps raw Android TouchState
            // packets to primaryTouch for ReadValueFromEvent, before allocation.
            int id; Vector2 point; TouchPhase phase;
            if (!screen.primaryTouch.touchId.ReadValueFromEvent(input, out id) ||
                !screen.primaryTouch.position.ReadValueFromEvent(input, out point) ||
                !screen.primaryTouch.phase.ReadValueFromEvent(input, out phase)) return;
            if (suspended) { input.handled = true; return; }
            if (phase == TouchPhase.Began && OwnedUi(point)) uiTouches.Add(id);
            if (uiTouches.Contains(id))
            {
                if (phase == TouchPhase.Ended || phase == TouchPhase.Canceled) uiTouches.Remove(id);
                return; // sticky ownership preserves controller/editor drags
            }
            input.handled = true;
            if (phase == TouchPhase.Began) gesture.Begin(id, point.x, point.y, input.time);
            else if (phase == TouchPhase.Moved || phase == TouchPhase.Stationary) gesture.Move(id, point.x, point.y, input.time);
            else if (phase == TouchPhase.Ended || phase == TouchPhase.Canceled)
                gesture.End(id, point.x, point.y, input.time, phase == TouchPhase.Canceled);
        }

        private void BeforeInput()
        {
            if (suspended || (InputState.currentUpdateType != InputUpdateType.Dynamic && InputState.currentUpdateType != InputUpdateType.Fixed)) return;
            buttons.BeginUpdate();
            gesture.Tick(InputState.currentTime);
        }

        private void Command(TouchPointerCommand command, float x, float y)
        {
            Vector2 previous = position;
            position = new Vector2(x, y);
            if (command == TouchPointerCommand.Tap) buttons.Tap();
            else if (command == TouchPointerCommand.Down) buttons.Hold(true);
            else if (command == TouchPointerCommand.Up) buttons.Hold(false);
            else Send(position - previous);
        }

        private void SetButton(bool pressed)
        {
            if (pressed) pressedFrame = Time.frameCount; else releasedFrame = Time.frameCount;
            Send(Vector2.zero);
        }

        private void Send(Vector2 delta)
        {
            if (mouse == null || !mouse.added) return;
            // A dedicated MouseState contains only the left button, no right.
            var state = new MouseState { position = position, delta = delta };
            state = state.WithButton(MouseButton.Left, buttons.Pressed);
            InputSystem.QueueStateEvent(mouse, state);
        }

        private void Suspend(bool value)
        {
            suspended = value;
            gesture?.Cancel(); buttons?.Cancel(); uiTouches.Clear();
        }
        private void OnApplicationPause(bool value) { Suspend(value); }
        private void OnApplicationFocus(bool focused) { Suspend(!focused); }
        private void OnDisable()
        {
            InputSystem.onEvent -= OnEvent; InputSystem.onBeforeUpdate -= BeforeInput;
            Suspend(true);
            if (mouse != null && mouse.added) InputSystem.RemoveDevice(mouse);
            mouse = null;
            if (instance == this) instance = null;
        }

        // Original MyInput uses legacy KeyCode calls. Merge only Mouse0 with
        // this pointer; real peripherals and every other key retain their path.
        public static bool GetKey(KeyCode key)
        { return Input.GetKey(key) || (key == KeyCode.Mouse0 && instance != null && instance.buttons.Pressed); }
        public static bool GetKeyDown(KeyCode key)
        { return Input.GetKeyDown(key) || (key == KeyCode.Mouse0 && instance != null && instance.pressedFrame == Time.frameCount); }
        public static bool GetKeyUp(KeyCode key)
        { return Input.GetKeyUp(key) || (key == KeyCode.Mouse0 && instance != null && instance.releasedFrame == Time.frameCount); }
    }
}
#endif
