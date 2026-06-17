const fs = require('fs');
const html = fs.readFileSync('courses.html', 'utf8');

const categories = [...html.matchAll(/class="filter-btn[^>]*>([^<]+)<\/button>/g)].map(m => m[1].trim());
console.log("CATEGORIES:\n", categories);

const courses = [...html.matchAll(/<div class="course-card[^>]*>([\s\S]*?)<\/div>\s*<\/div>/g)];
courses.forEach((c, i) => {
  const matchTitle = c[1].match(/<h3>([^<]+)<\/h3>/);
  const matchCategory = c[0].match(/data-category="([^"]+)"/);
  const title = matchTitle ? matchTitle[1] : "Unknown";
  const category = matchCategory ? matchCategory[1] : "Unknown";
  const hasImage = c[1].includes('<img');
  const hasLink = c[1].includes('<a href="') && !c[1].includes('<a href="#"');
  const hasPrice = c[1].includes('class="price"') || c[1].includes('Rs.');
  console.log(`Course ${i+1}: ${title} | Category: ${category} | Image: ${hasImage} | Link: ${hasLink} | Price: ${hasPrice}`);
});
