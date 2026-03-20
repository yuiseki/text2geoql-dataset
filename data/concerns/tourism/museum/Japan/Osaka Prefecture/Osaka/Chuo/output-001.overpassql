[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Chuo"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
