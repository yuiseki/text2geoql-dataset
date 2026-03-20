[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Nishinari Ward"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
