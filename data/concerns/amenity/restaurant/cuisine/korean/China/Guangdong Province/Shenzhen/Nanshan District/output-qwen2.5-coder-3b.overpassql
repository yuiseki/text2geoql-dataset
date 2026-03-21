[out:json][timeout:30];
area["name:en"="Nanshan District"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
