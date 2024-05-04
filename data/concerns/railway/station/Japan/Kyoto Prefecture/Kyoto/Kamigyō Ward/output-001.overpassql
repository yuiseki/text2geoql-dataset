[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Kamigyō Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
