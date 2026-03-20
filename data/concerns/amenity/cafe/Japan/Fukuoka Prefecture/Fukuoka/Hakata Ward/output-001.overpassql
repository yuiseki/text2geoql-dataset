[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Hakata Ward"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
