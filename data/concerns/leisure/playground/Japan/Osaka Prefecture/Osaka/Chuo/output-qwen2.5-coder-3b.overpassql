[out:json][timeout:30];
area["name:en"="Osaka Prefecture"]->.outer;
area["name:en"="Osaka"]->.inner;
(
  nwr["leisure"="playground"](area.inner)(area.outer);
);
out geom;
