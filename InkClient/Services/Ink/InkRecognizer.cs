using Contoso.NoteTaker.Http;
using Contoso.NoteTaker.JSON;
using Contoso.NoteTaker.JSON.Format;
using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using Windows.Graphics.Display;
using Windows.UI.Input.Inking;

using System.Net.Http;
using System.Text;

namespace Contoso.NoteTaker.Services.Ink
{
    public class InkRecognizer
    {
        List<InkRecognizerStroke> strokes;
        InkRecognitionRoot root = null;

        HttpManager httpManager;

        HttpClient httpClient = new HttpClient();
        public string json { get; set; }

        // Default DPI setting to use when device displayInfo is not set
        float dpiX = 96.0f;
        float dpiY = 96.0f;

        public InkRecognizer(string appKey, string baseAddress, string destinationUrl)
        {
            httpManager = new HttpManager(appKey, baseAddress, destinationUrl);
            strokes = new List<InkRecognizerStroke>();
        }

        public void AddStroke(InkStroke stroke)
        {
            var irStroke = new InkRecognizerStroke(stroke, dpiX, dpiY);
            strokes.Add(irStroke);
        }

        public void RemoveStroke(UInt64 strokeId)
        {
            var strokeToRemove = strokes.Find(stroke => stroke.Id == strokeId);
            strokes.Remove(strokeToRemove);
        }

        public void ClearStrokes()
        {
            strokes.Clear();
            root = null;
        }

        public void SetDisplayInformation(DisplayInformation displayInfo)
        {
            // DisplayInfo.RawDpiX and DisplayInfo.RawDpiY returns 0 when monitor doesnt provide physical dimensions 
            // or when user is in clone or multiple-monitor setup. Fallback to default DPI setting in such cases.
            dpiX = (displayInfo.RawDpiX != 0) ? displayInfo.RawDpiX : dpiX;
            dpiY = (displayInfo.RawDpiY != 0) ? displayInfo.RawDpiY : dpiY;
        }

        public InkRecognitionRoot GetRecognizerRoot()
        {
            return root;
        }

        public async Task<HttpStatusCode> RecognizeAsync()
        {
            try
            {
                var requestJson = JSONProcessor.CreateInkRecognitionRequest(strokes.AsReadOnly());
                var response = await httpManager.PutAsync(requestJson);
                var statusCode = response.StatusCode;
                if (statusCode == HttpStatusCode.OK)
                {
                    var responseJson = await response.Content.ReadAsStringAsync();
                    root = JSONProcessor.ParseInkRecognizerResponse(responseJson);
                    response = await TranslateAsync(responseJson);
                    json = await response.Content.ReadAsStringAsync();
                }
                return statusCode;
            }
            catch(Exception e)
            {
                throw;
            }
        }
        private async Task<HttpResponseMessage> TranslateAsync(string jsonRequest)
        {
            var httpContent = new StringContent(jsonRequest, Encoding.UTF8, "application/json");
            var httpResponse = await httpClient.PostAsync("https://educode.azure-api.net/EduCodeAPI/GenerateIntermediary/", httpContent);

            return httpResponse;
        }
    }


}
