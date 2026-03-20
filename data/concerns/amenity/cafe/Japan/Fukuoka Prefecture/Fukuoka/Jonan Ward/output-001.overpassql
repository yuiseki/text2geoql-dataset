[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Jonan Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
