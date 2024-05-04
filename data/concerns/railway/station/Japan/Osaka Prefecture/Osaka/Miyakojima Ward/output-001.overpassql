[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Miyakojima Ward"]->.inner;
(
  nwr["railway"="station"](area.inner)(area.outer);
);
out geom;
