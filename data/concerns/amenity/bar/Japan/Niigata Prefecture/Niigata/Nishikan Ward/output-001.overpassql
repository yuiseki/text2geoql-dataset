[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
area["name:en"="Nishikan Ward"]->.inner;
(
  nwr["amenity"="bar"](area.inner)(area.outer);
);
out geom;
