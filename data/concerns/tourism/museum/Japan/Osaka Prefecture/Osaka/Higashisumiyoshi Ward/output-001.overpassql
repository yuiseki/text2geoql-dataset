[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Higashisumiyoshi Ward"]->.inner;
(
  nwr["tourism"="museum"](area.inner)(area.outer);
);
out geom;
