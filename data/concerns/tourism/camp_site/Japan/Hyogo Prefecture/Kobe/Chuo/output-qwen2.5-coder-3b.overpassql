[out:json][timeout:30];
area["name:en"="Japan"][boundary=administrative]->.outer;
area["name:ja"="神奈川県"]->.inner;
(
  nwr["tourism"="camp_site"](area.inner)(area.outer);
);
out geom;
