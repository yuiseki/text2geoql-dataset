[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Osaka Prefecture"]->.inner;
(
  nwr["tourism"="picnic_site"](area.inner)(area.outer);
);
out geom;
