[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kamigyō Ward"]->.inner;
(
  nwr["historic"~"archaeological"](area.inner)(area.outer);
);
out geom;
