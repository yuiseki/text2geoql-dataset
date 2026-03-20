[out:json][timeout:30];
area["name:ja"="西区"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
