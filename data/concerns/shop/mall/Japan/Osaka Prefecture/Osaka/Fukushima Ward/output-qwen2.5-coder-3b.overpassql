[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Osaka Prefecture"]->.inner;
(
  nwr["shop"~"mall"](area.inner)(area.outer);
);
out geom;
