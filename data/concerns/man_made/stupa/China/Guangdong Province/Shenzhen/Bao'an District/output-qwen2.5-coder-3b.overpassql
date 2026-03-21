[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Guangdong Province"]->.inner;
(
  nwr["religion"~"buddhist"](area.inner)(area.outer);
);
out geom;
