[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:ja"="福岡市"]->.inner;
(
  nwr["amenity"~"university"](area.inner)(area.outer);
);
out geom;
