// LVII Co-living waitlist → Google Sheet
// 1. Open the Apps Script project (script.google.com) and paste this file.
// 2. Set SHEET_ID to the target sheet: the long ID in its URL,
//    https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit
//    Leave it empty to write to the sheet this script is bound to (the old behaviour).
// 3. Deploy → Manage deployments → Edit → Version: New version → Deploy.
//    Editing the existing deployment keeps the web app URL, so CONFIG.endpoint in the site stays the same.
//    Apps Script will ask you to re-authorise once, because it now opens a sheet by ID.
const SHEET_ID = '1tVbUe2JJuMH_z41tN9fxZEE328GvgWq14yGpA7Ak7-s'; // LVII Waitlist Leads (Maaef Media House account)
const COLUMNS = ['submitted_at','name','phone','email','profile','current_living','pain',
  'room_type','meals','budget','housing_pref','move_in','source'];

// Run this once from the editor (select "authorize" in the toolbar, then Run) to grant access
// before deploying. It only reads the sheet's name.
function authorize() {
  const book = SHEET_ID ? SpreadsheetApp.openById(SHEET_ID) : SpreadsheetApp.getActiveSpreadsheet();
  Logger.log('Connected to: ' + book.getName());
}

function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  if (data.company) return ContentService.createTextOutput('ok'); // honeypot filled: bot, don't save
  const book = SHEET_ID ? SpreadsheetApp.openById(SHEET_ID) : SpreadsheetApp.getActiveSpreadsheet();
  const sheet = book.getSheets()[0];
  if (sheet.getLastRow() === 0) sheet.appendRow(COLUMNS);
  sheet.appendRow(COLUMNS.map(k => data[k] || ''));
  return ContentService.createTextOutput('ok');
}
