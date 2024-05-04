// Important note: SubArea: Japan/Fukuoka Prefecture/Fukuoka
[out:json][timeout:30000];
area["name:en"="Fukuoka Prefecture"]->.outer;
area["name:en"="Fukuoka"]->.inner;
(
  relation["boundary"="administrative"]["admin_level"=8](area.inner)(area.outer);
);
out meta;
