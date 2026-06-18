const course = {is_free_preview: true};
const html = `<a href="foo" class="course-card-btn ${course.is_free_preview ? \'outline\' : \'\'}">text</a>`;
console.log(html);
