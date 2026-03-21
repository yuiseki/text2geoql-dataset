[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["leisure"="water_park"](area.inner)(area.outer);
);
out geom;
