[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Naniwa Ward"]->.inner;
(
  nwr["tourism"="guest_house"](area.inner)(area.outer);
);
out geom;
