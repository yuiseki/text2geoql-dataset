[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Fukuoka Prefecture"]->.inner;
(
  nwr["amenity"~"restaurant"](area.inner)(area.outer);
);
out geom;
