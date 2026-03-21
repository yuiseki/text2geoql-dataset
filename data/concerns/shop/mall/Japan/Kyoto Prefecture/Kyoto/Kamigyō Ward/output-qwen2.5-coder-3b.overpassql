[out:json][timeout:30];
area["name:en"="Kamigyō Ward"]->.outer;
area["name:en"="Kyoto"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
