[out:json][timeout:30];
area["name:en"="Hakata Ward"]->.outer;
area["name:ja"="福岡市"]->.inner;
(
  nwr["amenity"~"police"](area.inner)(area.outer);
);
out geom;
