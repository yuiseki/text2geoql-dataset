[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:ja"~"大阪"]->.inner;
(
  nwr["shop"~"bicycle"](area.inner)(area.outer);
);
out geom;
