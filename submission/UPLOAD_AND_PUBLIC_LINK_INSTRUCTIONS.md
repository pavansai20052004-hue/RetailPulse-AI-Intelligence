# Exact Upload and Public-Link Instructions

Follow these steps in order. Do not submit a localhost URL, local file path,
editable-only link, or link that requires the reviewer to request access.

## 1. Publish the Source Code

1. Create a GitHub repository named `RetailPulse`.
2. Set repository visibility to **Public**.
3. Upload or push the project files, excluding secrets, virtual environments,
   caches, and any data that cannot legally be redistributed.
4. Open the repository in a signed-out/private browser.
5. Copy the browser URL in this form:
   `https://github.com/<username>/RetailPulse`
6. Replace `<PUBLIC_GITHUB_REPOSITORY_URL>` in
   `submission/SUBMISSION_CHECKLIST.md`.

The source link must open the repository landing page, not a single file, branch
comparison, pull request, or GitHub settings page.

## 2. Publish the Live Deployment

The application is deployed from the repository's `render.yaml` Blueprint:

`https://retailpulse-9t0y.onrender.com`

The free Render service may need up to 50 seconds to wake after inactivity. Its
health endpoint is `https://retailpulse-9t0y.onrender.com/_stcore/health`.

## 3. Upload the Demo Video

Recommended path: YouTube as **Unlisted**.

1. Export the recording as MP4 at 1080p.
2. Upload it in YouTube Studio with the title
   `RetailPulse Project Demo`.
3. Set visibility to **Unlisted**, not Private.
4. Finish processing and verify that 1080p playback is available.
5. Open the share URL in a signed-out/private browser and play at least the
   opening, middle, and ending.
6. Copy the `https://youtu.be/<video-id>` URL.
7. Replace `<PUBLIC_DEMO_VIDEO_URL>` in
   `submission/SUBMISSION_CHECKLIST.md`.

Google Drive alternative:

1. Upload the MP4.
2. Select **Share**.
3. Under **General access**, choose **Anyone with the link**.
4. Set the role to **Viewer**.
5. Copy the link and test playback while signed out.

## 4. Upload the Feedback Reflection Video

1. Export the recording as MP4.
2. Upload it with the title `RetailPulse Feedback Reflection`.
3. Use YouTube **Unlisted** or Google Drive **Anyone with the link - Viewer**.
4. Test the video while signed out.
5. Replace `<PUBLIC_FEEDBACK_REFLECTION_VIDEO_URL>` in
   `submission/SUBMISSION_CHECKLIST.md`.

Do not reuse the demo URL unless the submission form explicitly requests one
combined video. The default assumption is that these are two separate links.

## 5. Upload the Project Report

Local source:
`output/pdf/RetailPulse_Final_Comprehensive_Report.pdf`

1. Upload that exact PDF to Google Drive.
2. Rename the Drive item to
   `RetailPulse_Final_Comprehensive_Report.pdf` if necessary.
3. Select **Share**.
4. Under **General access**, choose **Anyone with the link**.
5. Set the role to **Viewer**.
6. Copy the link.
7. Open it in a signed-out/private browser and confirm all six pages are visible.
8. Replace `<PUBLIC_PROJECT_REPORT_URL>` in
   `submission/SUBMISSION_CHECKLIST.md`.

Do not submit the local path, a `file:///` URL, or a link to the containing
folder. Submit the public link to the PDF itself.

## 6. Enter the Submission Form

1. Open `submission/SUBMISSION_CHECKLIST.md`.
2. Confirm that no `<PUBLIC_...>` placeholders remain.
3. Paste each URL into its matching form field.
4. Do not add Markdown, labels, quotation marks, or trailing punctuation.
5. Use the form's review/preview page to open each pasted URL.
6. Submit only after every link succeeds in a signed-out/private browser.
7. Save a screenshot or PDF of the confirmation page and retain the confirmation
   email.

## Public-Link Failure Fixes

| Symptom | Fix |
| --- | --- |
| "Request access" appears | Change sharing to **Anyone with the link - Viewer** |
| GitHub returns 404 while signed out | Change repository visibility to **Public** |
| YouTube says the video is private | Change visibility to **Unlisted** or **Public** |
| Streamlit asks for access | Deploy from a public repository or change app access |
| Streamlit shows an import error | Verify `requirements.txt` and the main file path |
| Streamlit shows missing data | Include only the permitted processed runtime data |
| Report link opens a folder | Share and copy the link for the PDF file itself |
