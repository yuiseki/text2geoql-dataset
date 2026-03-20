[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Miyakojima Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
