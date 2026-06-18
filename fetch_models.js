
async function getModels() {
  const response = await fetch('https://openrouter.ai/api/v1/models');
  const data = await response.json();
  const freeModels = data.data.filter(m => m.pricing.prompt === "0" && m.pricing.completion === "0");
  console.log('Free Models:');
  freeModels.slice(0, 15).forEach(m => console.log(m.id));
}

getModels();
