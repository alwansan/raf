#if UNITY_ANDROID && !UNITY_EDITOR
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.OnScreen;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;
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
        private readonly Dictionary<string, string> defaultPaths = new Dictionary<string, string>();
        // Closed allowlists prevent persisted settings from injecting arbitrary device paths.
        private static readonly string[] StickPaths = {
            "<Gamepad>/leftStick", "<Gamepad>/rightStick"
        };
        private static readonly string[] ButtonPaths = {
            "<Gamepad>/buttonSouth", "<Gamepad>/buttonEast",
            "<Gamepad>/buttonWest", "<Gamepad>/buttonNorth",
            "<Gamepad>/leftShoulder", "<Gamepad>/rightShoulder",
            "<Gamepad>/leftTrigger", "<Gamepad>/rightTrigger",
            "<Gamepad>/start", "<Gamepad>/select",
            "<Gamepad>/leftStickPress", "<Gamepad>/rightStickPress",
            "<Gamepad>/dpad/up", "<Gamepad>/dpad/down",
            "<Gamepad>/dpad/left", "<Gamepad>/dpad/right"
        };
        // Reuse the same buffer for bounded, read-only active action audits.
        // This does not change PlayerInput pairing or any original binding.
        private readonly List<InputAction> enabledActionAudit = new List<InputAction>(64);
        private int lastAuditedSceneHandle = -1;
        private bool editing;
        private string selected;
        public bool Visible { get { return visible; } }
        public bool Editing { get { return editing; } }
        public string SelectedControl { get { return selected ?? "none"; } }
        public string SelectedBinding
        {
            get { return selected != null && surfaces.ContainsKey(selected) ? GetBinding(selected) : "none"; }
        }

        public bool SetVisible(bool enabled)
        {
            if (enabled && !EnsureCanvas()) return false;
            if (!enabled && editing) SetLayoutEditMode(false);
            visible = enabled;
            if (canvasObject != null)
            {
                canvasObject.SetActive(enabled);
                if (enabled)
                {
                    UpdateSafeArea();
                    AuditVirtualBindings();
                }
            }
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
            // Configure paths before OnEnable can register a virtual device.
            canvasObject.SetActive(false);
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
            defaultPaths.Add(label, path);
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
            defaultPaths.Add(label, path);
            rect.gameObject.AddComponent<OnScreenButton>().controlPath = path;
        }

        private static bool IsAllowed(string path, string[] choices)
        {
            foreach (string candidate in choices)
                if (candidate == path) return true;
            return false;
        }

        private string GetBinding(string label)
        {
            var rect = surfaces[label];
            var stick = rect.GetComponent<OnScreenStick>();
            if (stick != null) return stick.controlPath;
            var button = rect.GetComponent<OnScreenButton>();
            return button != null ? button.controlPath : defaultPaths[label];
        }

        private static void ApplyControlPath(OnScreenControl widget, string path)
        {
            // Input System 1.7 re-runs SetupInputControl on every active setter,
            // even for the same path. Unregister first; never double-register.
            if (widget.controlPath == path) return;
            bool wasEnabled = widget.enabled;
            if (wasEnabled) widget.enabled = false;
            try
            {
                widget.controlPath = path;
            }
            finally
            {
                if (wasEnabled) widget.enabled = true;
            }
        }

        private void ApplyBinding(string label, string path)
        {
            var rect = surfaces[label];
            var stick = rect.GetComponent<OnScreenStick>();
            if (stick != null)
            {
                ApplyControlPath(stick, IsAllowed(path, StickPaths) ? path : defaultPaths[label]);
                return;
            }
            var button = rect.GetComponent<OnScreenButton>();
            if (button != null)
                ApplyControlPath(button, IsAllowed(path, ButtonPaths) ? path : defaultPaths[label]);
        }

        private void RestoreBinding(string label)
        {
            string saved = PlayerPrefs.GetString(LayoutKey + label + ".binding", defaultPaths[label]);
            ApplyBinding(label, saved);
        }

        public void CycleSelectedBinding(int delta)
        {
            // The on-screen controls are disabled in edit mode. Original action
            // assets and physical controller/keyboard bindings are untouched.
            if (!editing || selected == null || !surfaces.ContainsKey(selected)) return;
            var rect = surfaces[selected];
            string[] choices = rect.GetComponent<OnScreenStick>() != null ? StickPaths : ButtonPaths;
            int current = System.Array.IndexOf(choices, GetBinding(selected));
            if (current < 0) current = 0;
            int next = (current + (delta < 0 ? choices.Length - 1 : 1)) % choices.Length;
            ApplyBinding(selected, choices[next]);
            PlayerPrefs.SetString(LayoutKey + selected + ".binding", GetBinding(selected));
            PlayerPrefs.Save();
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", "touch_binding_changed",
                "control=" + selected + "; virtualPath=" + GetBinding(selected) +
                "; originalGameplayActionVerified=false");
        }

        public bool SetLayoutEditMode(bool enable)
        {
            if (enable && (!visible || canvasObject == null)) return false;
            // Exiting or entering edit mode can interrupt a touch without
            // dispatching pointer-up/OnDisable to its handle. Clear captures
            // before accepting another finger in the new mode.
            if (editing != enable)
            {
                foreach (var rect in surfaces.Values)
                {
                    var handle = rect.GetComponent<AndroidTouchLayoutHandle>();
                    if (handle != null) handle.CancelCapture();
                }
            }
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
            if (!enable) AuditVirtualBindings();
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
            ClampControlToSafeArea(label);
        }

        // Clamp the entire hit target, not just its center. Saved normalized
        // positions and original offsets can otherwise end up under a cutout
        // after rotation, a resolution change or a user-requested resize.
        private void ClampControlToSafeArea(string label)
        {
            if (safeRoot == null) return;
            Rect area = safeRoot.rect;
            if (area.width <= 0f || area.height <= 0f) return;
            var rect = surfaces[label];
            Vector2 offset = rect.anchoredPosition;
            Vector2 center = rect.anchorMin +
                new Vector2(offset.x / area.width, offset.y / area.height);
            float marginX = Mathf.Min(0.5f, rect.rect.width / (2f * area.width));
            float marginY = Mathf.Min(0.5f, rect.rect.height / (2f * area.height));
            Vector2 clamped = new Vector2(
                Mathf.Clamp(center.x, marginX, 1f - marginX),
                Mathf.Clamp(center.y, marginY, 1f - marginY));
            if (Mathf.Abs(center.x - clamped.x) > 0.0001f ||
                Mathf.Abs(center.y - clamped.y) > 0.0001f)
            {
                rect.anchorMin = rect.anchorMax = clamped;
                rect.anchoredPosition = Vector2.zero;
            }
        }

        private void ClampAllControlsToSafeArea()
        {
            foreach (string label in surfaces.Keys)
                ClampControlToSafeArea(label);
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
                ClampControlToSafeArea(label);
                Opacity(label, PlayerPrefs.GetFloat(key + "opacity", 0.36f));
                RestoreBinding(label);
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
                PlayerPrefs.DeleteKey(key + "binding");
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
            // An inactive canvas cannot complete a layout pass. Do not cache its
            // safe-area dimensions or the first visible frame may skip clamping.
            if (safeRoot == null || canvasObject == null || !canvasObject.activeInHierarchy ||
                Screen.width <= 0 || Screen.height <= 0) return;
            Rect area = Screen.safeArea;
            if (Screen.width == lastWidth && Screen.height == lastHeight && area == lastSafeArea) return;
            lastWidth = Screen.width;
            lastHeight = Screen.height;
            lastSafeArea = area;
            safeRoot.anchorMin = new Vector2(area.xMin / Screen.width, area.yMin / Screen.height);
            safeRoot.anchorMax = new Vector2(area.xMax / Screen.width, area.yMax / Screen.height);
            safeRoot.offsetMin = safeRoot.offsetMax = Vector2.zero;
            // RectTransform dimensions update at the canvas layout boundary.
            // Force one layout only on an actual safe-area/orientation change.
            Canvas.ForceUpdateCanvases();
            ClampAllControlsToSafeArea();
        }

        // Read-only evidence of whether the ORIGINAL enabled InputActions
        // actually resolve to the simulated Gamepad controls. Zero matches
        // is a useful diagnosis, not permission to rewrite the game actions.
        // Even positive matches do not prove gameplay response on a phone.
        public void AuditVirtualBindings()
        {
            if (!visible || editing || canvasObject == null ||
                !canvasObject.activeInHierarchy) return;
            lastAuditedSceneHandle = SceneManager.GetActiveScene().handle;
            enabledActionAudit.Clear();
            InputSystem.ListEnabledActions(enabledActionAudit);
            int resolved = 0, matched = 0;
            foreach (var entry in surfaces)
            {
                OnScreenControl widget = entry.Value.GetComponent<OnScreenStick>();
                if (widget == null) widget = entry.Value.GetComponent<OnScreenButton>();
                var virtualControl = widget != null ? widget.control : null;
                int count = 0;
                var actionNames = new StringBuilder();
                if (virtualControl != null)
                {
                    resolved++;
                    foreach (var action in enabledActionAudit)
                    {
                        foreach (var bound in action.controls)
                        {
                            // A gameplay action can bind to leftStick/x rather
                            // than leftStick. Walk parents without changing it.
                            bool consumesVirtualControl = false;
                            for (var current = bound; current != null; current = current.parent)
                                if (current == virtualControl)
                                {
                                    consumesVirtualControl = true;
                                    break;
                                }
                            if (!consumesVirtualControl) continue;
                            count++;
                            if (count <= 3)
                            {
                                if (actionNames.Length > 0) actionNames.Append(",");
                                // Names come from the game's action maps, not user input.
                                string actionName = action.name ?? "unnamed";
                                actionNames.Append(actionName.Substring(0, Mathf.Min(40, actionName.Length)));
                            }
                            break;
                        }
                    }
                }
                if (count > 0) matched++;
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", "touch_binding_audit",
                    "control=" + entry.Key + "; virtualPath=" + GetBinding(entry.Key) +
                    "; resolved=" + (virtualControl != null) +
                    "; enabledActionMatches=" + count + "; firstActions=" + actionNames +
                    "; gameplayResponseVerified=false");
            }
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", "touch_binding_audit_summary",
                "scene=" + lastAuditedSceneHandle + "; enabledActions=" + enabledActionAudit.Count +
                "; resolvedVirtualControls=" + resolved + "; controlsWithEnabledAction=" + matched +
                "; totalControls=" + surfaces.Count + "; gameplayResponseVerified=false");
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
                {
                    UpdateSafeArea();
                    if (!editing && SceneManager.GetActiveScene().handle != lastAuditedSceneHandle)
                        AuditVirtualBindings();
                }
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
        IPointerDownHandler, IDragHandler, IEndDragHandler, IPointerUpHandler
    {
        private const int NoPointer = int.MinValue;
        private AndroidTouchGamepadOverlay overlay;
        private string label;
        private int activePointerId = NoPointer;

        public void Bind(AndroidTouchGamepadOverlay owner, string control)
        {
            overlay = owner;
            label = control;
        }

        public void OnPointerDown(PointerEventData pointer)
        {
            // Capture one editing pointer per control. A second finger must not
            // hijack a drag or overwrite the first finger's saved position.
            if (overlay == null || !overlay.Editing || activePointerId != NoPointer) return;
            activePointerId = pointer.pointerId;
            overlay.Select(label);
        }

        public void OnDrag(PointerEventData pointer)
        {
            if (overlay != null && overlay.Editing && activePointerId == pointer.pointerId)
                overlay.Drag(label, pointer);
        }

        private void FinishPointer(PointerEventData pointer)
        {
            if (activePointerId != pointer.pointerId) return;
            try
            {
                if (overlay != null && overlay.Editing) overlay.SavePosition(label);
            }
            finally
            {
                activePointerId = NoPointer;
            }
        }

        // UI modules may dispatch pointer-up before end-drag or vice versa.
        // Whichever arrives first commits once and releases the capture.
        public void OnPointerUp(PointerEventData pointer)
        {
            FinishPointer(pointer);
        }

        public void OnEndDrag(PointerEventData pointer)
        {
            FinishPointer(pointer);
        }

        internal void CancelCapture()
        {
            activePointerId = NoPointer;
        }

        private void OnDisable()
        {
            // Scene/UI deactivation may omit pointer-up. Never retain a stale
            // touch ID when the editor is shown again.
            CancelCapture();
        }
    }
}
#endif
