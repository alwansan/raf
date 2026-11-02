#if UNITY_ANDROID && !UNITY_EDITOR
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.OnScreen;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;

namespace RaftAndroid.Platform
{
    // Opt-in first gameplay-touch slice: feed the ORIGINAL gamepad bindings
    // through Input System 1.7 on-screen controls. Never replace original
    // PlayerInput, action assets, UI modules, scenes or external peripherals.
    // This is NOT a complete mobile UI, layout editor or device validation.
    public sealed class AndroidTouchGamepadOverlay : MonoBehaviour
    {
        private GameObject canvasObject;
        private RectTransform safeRoot;
        private bool visible;
        private int lastWidth = -1, lastHeight = -1;
        private Rect lastSafeArea;
        public bool Visible { get { return visible; } }

        public bool SetVisible(bool enabled)
        {
            if (enabled && !EnsureCanvas()) return false;
            visible = enabled;
            if (canvasObject != null) canvasObject.SetActive(enabled);
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", "touch_gamepad_visible",
                "enabled=" + enabled + "; gamepadBindingExecutionVerified=false");
            return true;
        }

        private bool EnsureCanvas()
        {
            if (canvasObject != null) return true;
            // A second EventSystem or a replacement input module can break
            // original mouse, keyboard and menu navigation. Fail closed.
            var events = EventSystem.current;
            if (events == null || !events.isActiveAndEnabled ||
                events.GetComponent<InputSystemUIInputModule>() == null ||
                !events.GetComponent<InputSystemUIInputModule>().isActiveAndEnabled)
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", "touch_gamepad_unavailable",
                    "reason=original_input_system_ui_module_missing", true);
                return false;
            }
            canvasObject = new GameObject("RaftAndroidOptionalTouchGamepad",
                typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler),
                typeof(GraphicRaycaster));
            canvasObject.transform.SetParent(transform, false);
            var canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 1500;
            var scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = 0.5f;
            var safe = new GameObject("ScreenSafeArea", typeof(RectTransform));
            safe.transform.SetParent(canvasObject.transform, false);
            safeRoot = safe.GetComponent<RectTransform>();
            safeRoot.offsetMin = Vector2.zero;
            safeRoot.offsetMax = Vector2.zero;
            AddStick("Move", "<Gamepad>/leftStick", new Vector2(0f, 0f), new Vector2(190f, 180f));
            AddStick("Look", "<Gamepad>/rightStick", new Vector2(1f, 0f), new Vector2(-190f, 180f));
            AddButton("Interact", "<Gamepad>/buttonSouth", new Vector2(1f, 0f), new Vector2(-420f, 120f));
            AddButton("Action", "<Gamepad>/rightTrigger", new Vector2(1f, 0f), new Vector2(-370f, 285f));
            AddButton("Jump", "<Gamepad>/buttonNorth", new Vector2(1f, 0f), new Vector2(-210f, 360f));
            AddButton("Inventory", "<Gamepad>/buttonWest", new Vector2(0f, 0f), new Vector2(400f, 120f));
            AddButton("Menu", "<Gamepad>/start", new Vector2(1f, 1f), new Vector2(-105f, -90f));
            UpdateSafeArea();
            canvasObject.SetActive(false);
            return true;
        }

        private RectTransform AddSurface(string label, Vector2 anchor, Vector2 offset, float size)
        {
            var node = new GameObject(label, typeof(RectTransform), typeof(Image));
            node.transform.SetParent(safeRoot, false);
            var rect = node.GetComponent<RectTransform>();
            rect.anchorMin = rect.anchorMax = anchor;
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.sizeDelta = new Vector2(size, size);
            rect.anchoredPosition = offset;
            var image = node.GetComponent<Image>();
            image.color = new Color(0.25f, 0.32f, 0.4f, 0.36f);
            image.raycastTarget = true;
            var caption = new GameObject("Label", typeof(RectTransform), typeof(Text));
            caption.transform.SetParent(node.transform, false);
            var textRect = caption.GetComponent<RectTransform>();
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.offsetMin = textRect.offsetMax = Vector2.zero;
            var text = caption.GetComponent<Text>();
            text.text = label;
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.fontSize = 22;
            text.alignment = TextAnchor.MiddleCenter;
            text.color = Color.white;
            text.raycastTarget = false;
            return rect;
        }

        private void AddStick(string label, string path, Vector2 anchor, Vector2 offset)
        {
            var rect = AddSurface(label, anchor, offset, 190f);
            var stick = rect.gameObject.AddComponent<OnScreenStick>();
            stick.controlPath = path;
            stick.movementRange = 110f;
            // Keep pointer actions isolated when PlayerInput switches to the
            // virtual Gamepad, preventing pointer-up jitter on drag.
            stick.useIsolatedInputActions = true;
        }

        private void AddButton(string label, string path, Vector2 anchor, Vector2 offset)
        {
            var rect = AddSurface(label, anchor, offset, 100f);
            rect.gameObject.AddComponent<OnScreenButton>().controlPath = path;
        }

        private void UpdateSafeArea()
        {
            if (safeRoot == null || Screen.width <= 0 || Screen.height <= 0) return;
            Rect area = Screen.safeArea;
            if (Screen.width == lastWidth && Screen.height == lastHeight && area == lastSafeArea) return;
            lastWidth = Screen.width;
            lastHeight = Screen.height;
            lastSafeArea = area;
            safeRoot.anchorMin = new Vector2(area.xMin / Screen.width, area.yMin / Screen.height);
            safeRoot.anchorMax = new Vector2(area.xMax / Screen.width, area.yMax / Screen.height);
            safeRoot.offsetMin = safeRoot.offsetMax = Vector2.zero;
        }

        private void Update()
        {
            if (visible)
            {
                // If the original UI input module disappears during scene
                // transitions, remove virtual input instead of stealing events.
                var events = EventSystem.current;
                if (events == null || !events.isActiveAndEnabled ||
                    events.GetComponent<InputSystemUIInputModule>() == null ||
                    !events.GetComponent<InputSystemUIInputModule>().isActiveAndEnabled)
                    SetVisible(false);
                else
                    UpdateSafeArea();
            }
        }

        private void OnDisable()
        {
            visible = false;
            if (canvasObject != null) canvasObject.SetActive(false);
        }
    }
}
#endif
