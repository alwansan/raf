#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;

namespace RaftAndroid.Platform
{
    // Authored controls use the game's existing InputSystemUIInputModule.
    // IMGUI buttons cannot depend on legacy touch-to-left-mouse simulation:
    // the original CustomInputConfig intentionally disables that simulation.
    public sealed class AndroidTouchUiPanel : MonoBehaviour
    {
        private GameObject canvasObject, editorObject, reportObject;
        private RectTransform safeRoot;
        private readonly RectTransform[] rightButtons = new RectTransform[3];
        private static readonly float[] RightButtonOffsets = { 78f, 126f, 174f };
        private AndroidTouchGamepadOverlay gamepad;
        private AndroidTestDiagnostics diagnostics;
        private Text toggleText, selectionText, bindingText, reportText;
        private Slider opacity;
        private bool reportOpen;
        private float nextReport;
        public bool Ready { get { return canvasObject != null && canvasObject.activeInHierarchy; } }

        private void Update()
        {
            var events = EventSystem.current;
            var module = events != null ? events.GetComponent<InputSystemUIInputModule>() : null;
            bool available = module != null && module.isActiveAndEnabled;
            if (canvasObject == null && available) Create();
            if (canvasObject == null) return;
            canvasObject.SetActive(available);
            if (!available) return;
            Rect safe = Screen.safeArea;
            safeRoot.anchorMin = new Vector2(safe.xMin / Screen.width, safe.yMin / Screen.height);
            safeRoot.anchorMax = new Vector2(safe.xMax / Screen.width, safe.yMax / Screen.height);
            safeRoot.offsetMin = safeRoot.offsetMax = Vector2.zero;
            FitPanelsToSafeArea(safe);
            FitRightButtonsToSafeArea(safe);
            toggleText.text = gamepad.Visible ? "Hide Xbox" : "Show Xbox";
            editorObject.SetActive(gamepad.Visible && gamepad.Editing);
            reportObject.SetActive(reportOpen && !gamepad.Editing);
            selectionText.text = "Selected: " + gamepad.SelectedControl + "   (drag to move)";
            bindingText.text = "Binding: " + gamepad.SelectedBinding;
            opacity.SetValueWithoutNotify(gamepad.GlobalOpacity);
            if (reportObject.activeSelf && Time.unscaledTime >= nextReport)
            {
                nextReport = Time.unscaledTime + 1f;
                reportText.text = diagnostics.TouchReportPreview();
            }
        }

        private void Create()
        {
            gamepad = GetComponent<AndroidTouchGamepadOverlay>();
            diagnostics = GetComponent<AndroidTestDiagnostics>();
            canvasObject = new GameObject("RaftAndroidTouchPanel", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvasObject.transform.SetParent(transform, false);
            var canvas = canvasObject.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 1600;
            var scaler = canvasObject.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 720);
            scaler.matchWidthOrHeight = 1f;
            safeRoot = Node("SafeArea", canvasObject.transform, 0, 0, 0, 0);
            // Block game UI behind the non-interactive performance bar.
            var bar = Node("HudTouchBlocker", safeRoot, 0, 0, 1920, 70);
            bar.gameObject.AddComponent<Image>().color = Color.clear;
            AddRightButton(safeRoot, "Show Xbox", 8, 78, 150, () => gamepad.SetVisible(!gamepad.Visible), out toggleText);
            rightButtons[0] = safeRoot.Find("Show Xbox") as RectTransform;
            AddRightButton(safeRoot, "Xbox layout", 8, 126, 150, () =>
            {
                if (!gamepad.Visible) gamepad.SetVisible(true);
                gamepad.SetLayoutEditMode(!gamepad.Editing);
                reportOpen = false;
            });
            rightButtons[1] = safeRoot.Find("Xbox layout") as RectTransform;
            AddRightButton(safeRoot, "Test report", 8, 174, 150, () => { reportOpen = !reportOpen; gamepad.SetLayoutEditMode(false); });
            rightButtons[2] = safeRoot.Find("Test report") as RectTransform;
            editorObject = Panel("Xbox layout editor", 500, 252);
            var edit = editorObject.GetComponent<RectTransform>();
            selectionText = Label(edit, "Select a controller button", 12, 10, 476, 30);
            AddButton(edit, "Size -", 12, 45, 112, () => gamepad.AdjustSelectedSize(-15));
            AddButton(edit, "Size +", 132, 45, 112, () => gamepad.AdjustSelectedSize(15));
            AddButton(edit, "Reset", 252, 45, 112, () => gamepad.ResetLayout());
            bindingText = Label(edit, "Binding: none", 12, 91, 476, 22);
            bindingText.fontSize = 14;
            Label(edit, "Controller transparency", 12, 115, 460, 24);
            var sliderRoot = Node("GlobalOpacity", edit, 16, 145, 460, 32);
            sliderRoot.gameObject.AddComponent<Image>().color = new Color(.2f, .2f, .2f, 1);
            opacity = sliderRoot.gameObject.AddComponent<Slider>();
            opacity.navigation = new Navigation { mode = Navigation.Mode.None };
            opacity.minValue = .2f; opacity.maxValue = .95f;
            var handle = Node("Handle", sliderRoot, 0, 0, 28, 32);
            var handleImage = handle.gameObject.AddComponent<Image>(); handleImage.color = Color.white;
            opacity.handleRect = handle; opacity.targetGraphic = handleImage;
            opacity.onValueChanged.AddListener(value => gamepad.SetGlobalOpacity(value));
            AddButton(edit, "Finish editing", 12, 204, 220, () => gamepad.SetLayoutEditMode(false));
            AddButton(edit, "Bind -", 252, 204, 112, () => gamepad.CycleSelectedBinding(-1));
            AddButton(edit, "Bind +", 372, 204, 112, () => gamepad.CycleSelectedBinding(1));
            reportObject = Panel("Local test report", 650, 440);
            var report = reportObject.GetComponent<RectTransform>();
            AddButton(report, "Copy report", 12, 8, 200, () => diagnostics.CopyTouchReport());
            AddButton(report, "Close", 220, 8, 120, () => reportOpen = false);
            var viewport = Node("Viewport", report, 12, 60, 626, 366);
            viewport.gameObject.AddComponent<Image>().color = Color.black;
            viewport.gameObject.AddComponent<RectMask2D>();
            reportText = Label(viewport, "", 0, 0, 626, 366);
            reportText.fontSize = 15;
            reportText.horizontalOverflow = HorizontalWrapMode.Wrap;
            reportText.verticalOverflow = VerticalWrapMode.Overflow;
            var content = reportText.rectTransform;
            content.gameObject.AddComponent<ContentSizeFitter>().verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            var scroll = viewport.gameObject.AddComponent<ScrollRect>();
            scroll.horizontal = false; scroll.viewport = viewport; scroll.content = content;
            scroll.movementType = ScrollRect.MovementType.Clamped;
            editorObject.SetActive(false); reportObject.SetActive(false);
        }

        // The original 720-unit panel layout ends at y=668. On shorter
        // Android safe areas (letterbox/cutout/multi-window), fixed panels
        // otherwise lose their bottom buttons. Scale the existing panels,
        // not the three top-right diagnostic buttons or gameplay controls.
        private void FitPanelsToSafeArea(Rect safe)
        {
            if (Screen.height <= 0 || Screen.width <= 0) return;
            float canvasScale = Screen.height / 720f; // CanvasScaler matches height.
            float safeHeight = safe.height / canvasScale;
            float safeWidth = safe.width / canvasScale;
            float factor = Mathf.Clamp(Mathf.Min(safeHeight / 684f, safeWidth / 666f), 0.1f, 1f);
            FitPanel(editorObject, factor);
            FitPanel(reportObject, factor);
        }

        // Keep all three diagnostic actions reachable on unusually short safe
        // areas. Their original top offsets (78/126/174) and 42-unit height
        // fit in 216 units; scaling the entire stack preserves spacing.
        // Only these diagnostic buttons are scaled; gamepad controls are not.
        private void FitRightButtonsToSafeArea(Rect safe)
        {
            if (Screen.height <= 0 || Screen.width <= 0 || safeRoot == null) return;
            // CanvasScaler matches height: both safe-area dimensions must be
            // expressed in the same 720-reference units as the buttons.
            float canvasScale = Screen.height / 720f;
            float safeHeight = safe.height / canvasScale;
            float safeWidth = safe.width / canvasScale;
            // A height-only clamp clips the 150-unit buttons on narrow safe
            // areas (multi-window, display cutouts or external displays).
            // Include the 8-unit right inset and avoid a positive minimum
            // scale that would force controls outside very small safe areas.
            float factor = Mathf.Clamp01(Mathf.Min(safeHeight / 224f, safeWidth / 166f));
            for (int i = 0; i < rightButtons.Length; i++)
            {
                var child = rightButtons[i];
                if (child == null) continue;
                child.localScale = new Vector3(factor, factor, 1f);
                child.anchoredPosition = new Vector2(-8f * factor, -RightButtonOffsets[i] * factor);
            }
        }

        private static void FitPanel(GameObject panel, float factor)
        {
            if (panel == null) return;
            var rect = panel.GetComponent<RectTransform>();
            rect.localScale = new Vector3(factor, factor, 1f);
            rect.anchoredPosition = new Vector2(0f, -228f * factor);
        }

        private GameObject Panel(string name, float width, float height)
        {
            var rect = Node(name, safeRoot, 8, 228, width, height);
            rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(.5f, 1);
            rect.anchoredPosition = new Vector2(0, -228);
            rect.gameObject.AddComponent<Image>().color = new Color(0, 0, 0, .95f);
            return rect.gameObject;
        }

        private static RectTransform Node(string name, Transform parent, float x, float y, float width, float height)
        {
            var node = new GameObject(name, typeof(RectTransform)); node.transform.SetParent(parent, false);
            var rect = node.GetComponent<RectTransform>();
            rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = new Vector2(x, -y); rect.sizeDelta = new Vector2(width, height);
            return rect;
        }

        private static Text Label(Transform parent, string caption, float x, float y, float width, float height)
        {
            var rect = Node("Label", parent, x, y, width, height);
            var text = rect.gameObject.AddComponent<Text>();
            text.text = caption; text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.fontSize = 18; text.color = Color.white; text.raycastTarget = false;
            return text;
        }

        private static void AddButton(Transform parent, string caption, float x, float y, float width, Action pressed)
        { Text unused; AddButton(parent, caption, x, y, width, pressed, out unused); }

        private static void AddButton(Transform parent, string caption, float x, float y, float width, Action pressed, out Text label)
        {
            var rect = Node(caption, parent, x, y, width, 42);
            var image = rect.gameObject.AddComponent<Image>(); image.color = new Color(.12f, .16f, .2f, .96f);
            var button = rect.gameObject.AddComponent<Button>(); button.targetGraphic = image;
            button.navigation = new Navigation { mode = Navigation.Mode.None };
            button.onClick.AddListener(() => pressed());
            label = Label(rect, caption, 0, 0, width, 42); label.alignment = TextAnchor.MiddleCenter;
        }

        // Diagnostic actions live against the RIGHT edge of Screen.safeArea,
        // independent of resolution/aspect ratio and without moving gameplay controls.
        private static void AddRightButton(Transform parent, string caption, float inset, float y, float width, Action pressed, out Text label)
        {
            var rect = Node(caption, parent, 0, y, width, 42);
            rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(1, 1);
            rect.anchoredPosition = new Vector2(-inset, -y);
            var image = rect.gameObject.AddComponent<Image>();
            image.color = new Color(.12f, .16f, .2f, .96f);
            var button = rect.gameObject.AddComponent<Button>();
            button.targetGraphic = image;
            button.navigation = new Navigation { mode = Navigation.Mode.None };
            button.onClick.AddListener(() => pressed());
            label = Label(rect, caption, 0, 0, width, 42);
            // The button's pivot is top-right; stretch its caption inside
            // that rect rather than placing the label to its right.
            var captionRect = label.rectTransform;
            captionRect.anchorMin = Vector2.zero;
            captionRect.anchorMax = Vector2.one;
            captionRect.offsetMin = captionRect.offsetMax = Vector2.zero;
            label.alignment = TextAnchor.MiddleCenter;
        }

        private static void AddRightButton(Transform parent, string caption, float inset, float y, float width, Action pressed)
        {
            Text unused;
            AddRightButton(parent, caption, inset, y, width, pressed, out unused);
        }

        private void OnDisable() { if (canvasObject != null) canvasObject.SetActive(false); }
    }
}
#endif
