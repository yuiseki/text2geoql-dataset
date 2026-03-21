[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:ja"="福岡県"]->.inner;
(
  nwr["amenity"~"hospital|clinic"](area.inner)(area.outer);
);
out geom;
