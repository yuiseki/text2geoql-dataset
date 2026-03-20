[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Yangcheon-gu"]->.inner;
(
  nwr["tourism"="camp_site"](area.inner)(area.outer);
);
out geom;
