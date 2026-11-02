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
        private AndroidTouchGamepadOverlay gamepad;
        private AndroidTestDiagnostics diagnostics;
        private Text toggleText, selectionText, reportText;
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
            toggleText.text = gamepad.Visible ? "Hide Xbox" : "Show Xbox";
            editorObject.SetActive(gamepad.Visible && gamepad.Editing);
            reportObject.SetActive(reportOpen && !gamepad.Editing);
            selectionText.text = "Selected: " + gamepad.SelectedControl + "   (drag to move)";
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
            AddButton(safeRoot, "Show Xbox", 8, 78, 150, () => gamepad.SetVisible(!gamepad.Visible), out toggleText);
            AddButton(safeRoot, "Xbox layout", 8, 126, 150, () =>
            {
                if (!gamepad.Visible) gamepad.SetVisible(true);
                gamepad.SetLayoutEditMode(!gamepad.Editing);
                reportOpen = false;
            });
            AddButton(safeRoot, "Test report", 8, 174, 150, () => { reportOpen = !reportOpen; gamepad.SetLayoutEditMode(false); });
            editorObject = Panel("Xbox layout editor", 500, 252);
            var edit = editorObject.GetComponent<RectTransform>();
            selectionText = Label(edit, "Select a controller button", 12, 10, 476, 30);
            AddButton(edit, "Size -", 12, 45, 112, () => gamepad.AdjustSelectedSize(-15));
            AddButton(edit, "Size +", 132, 45, 112, () => gamepad.AdjustSelectedSize(15));
            AddButton(edit, "Reset", 252, 45, 112, () => gamepad.ResetLayout());
            Label(edit, "Controller transparency", 12, 98, 460, 28);
            var sliderRoot = Node("GlobalOpacity", edit, 16, 134, 460, 32);
            sliderRoot.gameObject.AddComponent<Image>().color = new Color(.2f, .2f, .2f, 1);
            opacity = sliderRoot.gameObject.AddComponent<Slider>();
            opacity.navigation = new Navigation { mode = Navigation.Mode.None };
            opacity.minValue = .2f; opacity.maxValue = .95f;
            var handle = Node("Handle", sliderRoot, 0, 0, 28, 32);
            var handleImage = handle.gameObject.AddComponent<Image>(); handleImage.color = Color.white;
            opacity.handleRect = handle; opacity.targetGraphic = handleImage;
            opacity.onValueChanged.AddListener(value => gamepad.SetGlobalOpacity(value));
            AddButton(edit, "Finish editing", 12, 190, 220, () => gamepad.SetLayoutEditMode(false));
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

        private void OnDisable() { if (canvasObject != null) canvasObject.SetActive(false); }
    }
}
#endif
