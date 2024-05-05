[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kamigyō Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
