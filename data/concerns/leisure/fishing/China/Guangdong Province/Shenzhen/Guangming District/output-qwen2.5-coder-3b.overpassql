[out:json][timeout:30];
area["name:en"="Guangdong Province"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["leisure"="fishing"](area.inner)(area.outer);
);
out geom;
