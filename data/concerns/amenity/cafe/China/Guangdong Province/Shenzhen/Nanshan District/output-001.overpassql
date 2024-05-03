[out:json][timeout:30000];
area["name:en"="Shenzhen"]->.outer;
area["name:en"="Nanshan District"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
