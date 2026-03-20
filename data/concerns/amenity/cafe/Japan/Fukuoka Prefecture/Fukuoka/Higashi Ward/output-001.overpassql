[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
