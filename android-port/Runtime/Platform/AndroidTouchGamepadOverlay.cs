#if UNITY_ANDROID && !UNITY_EDITOR
using System.Collections.Generic;
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
        private const string LayoutKey = "raft.android.touchlayout.v1.";
        private readonly Dictionary<string, RectTransform> surfaces = new Dictionary<string, RectTransform>();
        private readonly Dictionary<string, Vector2> defaults = new Dictionary<string, Vector2>();
        private readonly Dictionary<string, Vector2> defaultOffsets = new Dictionary<string, Vector2>();
        private readonly Dictionary<string, float> defaultSizes = new Dictionary<string, float>();
        private bool editing;
        private string selected;
        public bool Visible { get { return visible; } }
        public bool Editing { get { return editing; } }
        public string SelectedControl { get { return selected ?? "none"; } }

        public bool SetVisible(bool enabled)
        {
            if (enabled && !EnsureCanvas()) return false;
            if (!enabled && editing) SetLayoutEditMode(false);
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
            RestoreLayout();
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
            surfaces.Add(label, rect);
            defaults.Add(label, anchor);
            defaultOffsets.Add(label, offset);
            defaultSizes.Add(label, size);
            node.AddComponent<AndroidTouchLayoutHandle>().Bind(this, label);
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

        public bool SetLayoutEditMode(bool enable)
        {
            if (enable && (!visible || canvasObject == null)) return false;
            editing = enable;
            selected = null;
            foreach (var rect in surfaces.Values)
            {
                var stick = rect.GetComponent<OnScreenStick>();
                if (stick != null) stick.enabled = !enable;
                var button = rect.GetComponent<OnScreenButton>();
                if (button != null) button.enabled = !enable;
            }
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", "touch_layout_edit",
                "enabled=" + enable + "; gameplayInputSuppressed=" + enable);
            return true;
        }

        private static float SafeFloat(float value, float fallback)
        {
            return float.IsNaN(value) || float.IsInfinity(value) ? fallback : value;
        }

        private void Resize(string label, float size)
        {
            var rect = surfaces[label];
            size = Mathf.Clamp(SafeFloat(size, defaultSizes[label]), 70f, 280f);
            rect.sizeDelta = new Vector2(size, size);
            var stick = rect.GetComponent<OnScreenStick>();
            if (stick != null) stick.movementRange = Mathf.Min(110f, size * 0.55f);
        }

        private void Opacity(string label, float alpha)
        {
            alpha = Mathf.Clamp(SafeFloat(alpha, 0.36f), 0.2f, 0.95f);
            var rect = surfaces[label];
            var image = rect.GetComponent<Image>();
            var color = image.color;
            color.a = alpha;
            image.color = color;
            var caption = rect.GetComponentInChildren<Text>();
            if (caption != null)
            {
                color = caption.color;
                color.a = alpha;
                caption.color = color;
            }
        }

        private void RestoreLayout()
        {
            foreach (var entry in surfaces)
            {
                string label = entry.Key;
                var rect = entry.Value;
                string key = LayoutKey + label + ".";
                rect.anchorMin = rect.anchorMax = defaults[label];
                rect.anchoredPosition = defaultOffsets[label];
                if (PlayerPrefs.HasKey(key + "x") && PlayerPrefs.HasKey(key + "y"))
                {
                    float x = SafeFloat(PlayerPrefs.GetFloat(key + "x"), defaults[label].x);
                    float y = SafeFloat(PlayerPrefs.GetFloat(key + "y"), defaults[label].y);
                    rect.anchorMin = rect.anchorMax = new Vector2(Mathf.Clamp01(x), Mathf.Clamp01(y));
                    rect.anchoredPosition = Vector2.zero;
                }
                Resize(label, PlayerPrefs.GetFloat(key + "size", defaultSizes[label]));
                Opacity(label, PlayerPrefs.GetFloat(key + "opacity", 0.36f));
            }
        }

        public void ResetLayout()
        {
            foreach (string label in surfaces.Keys)
            {
                string key = LayoutKey + label + ".";
                PlayerPrefs.DeleteKey(key + "x");
                PlayerPrefs.DeleteKey(key + "y");
                PlayerPrefs.DeleteKey(key + "size");
                PlayerPrefs.DeleteKey(key + "opacity");
            }
            PlayerPrefs.Save();
            selected = null;
            RestoreLayout();
        }

        public void AdjustSelectedSize(float delta)
        {
            if (!editing || selected == null) return;
            Resize(selected, surfaces[selected].sizeDelta.x + delta);
            PlayerPrefs.SetFloat(LayoutKey + selected + ".size", surfaces[selected].sizeDelta.x);
            PlayerPrefs.Save();
        }

        public void AdjustSelectedOpacity(float delta)
        {
            if (!editing || selected == null) return;
            float alpha = surfaces[selected].GetComponent<Image>().color.a + delta;
            Opacity(selected, alpha);
            PlayerPrefs.SetFloat(LayoutKey + selected + ".opacity",
                surfaces[selected].GetComponent<Image>().color.a);
            PlayerPrefs.Save();
        }

        internal void Select(string label)
        {
            if (editing && surfaces.ContainsKey(label)) selected = label;
        }

        internal void Drag(string label, PointerEventData pointer)
        {
            if (!editing || safeRoot == null || !surfaces.ContainsKey(label)) return;
            Vector2 local;
            if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(
                safeRoot, pointer.position, pointer.pressEventCamera, out local)) return;
            Rect area = safeRoot.rect;
            if (area.width <= 0 || area.height <= 0) return;
            var rect = surfaces[label];
            float marginX = Mathf.Min(0.5f, rect.rect.width / (2f * area.width));
            float marginY = Mathf.Min(0.5f, rect.rect.height / (2f * area.height));
            float x = Mathf.Clamp(local.x / area.width + safeRoot.pivot.x, marginX, 1f - marginX);
            float y = Mathf.Clamp(local.y / area.height + safeRoot.pivot.y, marginY, 1f - marginY);
            rect.anchorMin = rect.anchorMax = new Vector2(x, y);
            rect.anchoredPosition = Vector2.zero;
            selected = label;
        }

        internal void SavePosition(string label)
        {
            if (!editing || !surfaces.ContainsKey(label)) return;
            Vector2 position = surfaces[label].anchorMin;
            PlayerPrefs.SetFloat(LayoutKey + label + ".x", position.x);
            PlayerPrefs.SetFloat(LayoutKey + label + ".y", position.y);
            PlayerPrefs.Save();
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
            if (editing) SetLayoutEditMode(false);
            visible = false;
            if (canvasObject != null) canvasObject.SetActive(false);
        }
    }

    public sealed class AndroidTouchLayoutHandle : MonoBehaviour,
        IPointerDownHandler, IDragHandler, IEndDragHandler
    {
        private AndroidTouchGamepadOverlay overlay;
        private string label;

        public void Bind(AndroidTouchGamepadOverlay owner, string control)
        {
            overlay = owner;
            label = control;
        }

        public void OnPointerDown(PointerEventData pointer)
        {
            if (overlay != null) overlay.Select(label);
        }

        public void OnDrag(PointerEventData pointer)
        {
            if (overlay != null) overlay.Drag(label, pointer);
        }

        public void OnEndDrag(PointerEventData pointer)
        {
            if (overlay != null) overlay.SavePosition(label);
        }
    }
}
#endif
