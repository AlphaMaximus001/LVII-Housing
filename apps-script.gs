// LVII Co-living waitlist → Google Sheet
// 1. Create a Google Sheet. Extensions → Apps Script. Paste this file.
// 2. Deploy → New deployment → Web app. Execute as: Me. Who has access: Anyone.
// 3. Copy the web app URL into CONFIG.endpoint in the website.
const COLUMNS = ['submitted_at','name','phone','email','profile','current_living','pain',
  'room_type','meals','budget','housing_pref','move_in','source'];

function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (sheet.getLastRow() === 0) sheet.appendRow(COLUMNS);
  const data = JSON.parse(e.postData.contents);
  sheet.appendRow(COLUMNS.map(k => data[k] || ''));
  return ContentService.createTextOutput('ok');
}
