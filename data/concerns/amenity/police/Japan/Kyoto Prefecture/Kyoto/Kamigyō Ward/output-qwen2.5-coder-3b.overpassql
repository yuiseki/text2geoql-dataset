[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kamigyō Ward"]->.inner;
(
  nwr["amenity"~"police"](area.inner)(area.outer);
);
out geom;
