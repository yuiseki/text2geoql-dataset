[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Akiha Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
