const fs = require('fs');
const html = fs.readFileSync('admin.html', 'utf8');
const scriptMatches = html.match(/<script>([\s\S]*?)<\/script>/gi);
if (scriptMatches) {
  scriptMatches.forEach((script, i) => {
    const code = script.replace(/<\/?script>/g, '');
    try {
      new Function(code);
      console.log(`Script ${i} parses successfully.`);
    } catch (e) {
      console.log(`Script ${i} parsing error:`, e.message);
    }
  });
} else {
  console.log("No scripts found!");
}
