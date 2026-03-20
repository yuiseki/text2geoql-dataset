[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Naniwa Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
