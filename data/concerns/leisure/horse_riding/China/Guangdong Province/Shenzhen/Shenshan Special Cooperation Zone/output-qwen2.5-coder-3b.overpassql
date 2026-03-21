[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["leisure"="horse_riding"](area.inner)(area.outer);
);
out geom;
