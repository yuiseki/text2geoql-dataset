// Important note: Never use "landuse"="factory". It is wrong. Use "landuse"="industrial" instead.
[out:json][timeout:30000];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["landuse"="industrial"](area.inner)(area.outer);
);
out geom;
