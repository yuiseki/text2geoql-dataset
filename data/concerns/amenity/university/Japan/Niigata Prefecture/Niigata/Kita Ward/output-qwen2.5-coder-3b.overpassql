[out:json][timeout:30];
area["name:ja"="北区"]->.outer;
area["name:en"="Kita Ward"]->.inner;
(
  nwr["amenity"="university"](area.inner)(area.outer);
);
out geom;
