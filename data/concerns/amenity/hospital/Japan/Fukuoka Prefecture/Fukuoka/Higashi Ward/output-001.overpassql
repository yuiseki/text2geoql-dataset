[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["amenity"="hospital"](area.inner)(area.outer);
);
out geom;
