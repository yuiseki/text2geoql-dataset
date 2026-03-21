[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:ja"="福岡市"]->.inner;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
