// Important note: Never use "amenity"="church". It is wrong. Use "building"="church" instead.
[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Taito"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
