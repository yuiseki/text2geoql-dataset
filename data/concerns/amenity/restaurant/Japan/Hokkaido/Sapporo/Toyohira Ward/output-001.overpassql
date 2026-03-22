[out:json][timeout:30];
area["name:en"="Sapporo"]->.outer;
area["name:en"="Toyohira Ward"]->.inner;
(
  nwr["amenity"="restaurant"](area.inner)(area.outer);
);
out geom;